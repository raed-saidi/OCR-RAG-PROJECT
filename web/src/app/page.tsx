"use client"

import type React from "react"

import { useState } from "react"
import {
  Box,
  Button,
  Input,
  Text,
  VStack,
  Heading,
  Container,
  InputGroup,
  InputRightElement,
  Card,
  CardBody,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast,
} from "@chakra-ui/react"
import { SearchIcon } from "@chakra-ui/icons"

interface Document {
  path: string
  full_path?: string
  score: number
}

interface RAGResponse {
  success: boolean
  answer?: string
  documents?: Document[]
  error?: string
}

export default function Home() {
  const [query, setQuery] = useState("")
  const [answer, setAnswer] = useState("")
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const toast = useToast()

  const handleSearch = async () => {
    if (!query.trim()) {
      toast({
        title: "Erreur",
        description: "Veuillez entrer une question",
        status: "warning",
        duration: 3000,
      })
      return
    }

    setIsLoading(true)
    setError("")
    setAnswer("")
    setDocuments([])

    try {
      const res = await fetch("/api/rag", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      })

      const data: RAGResponse = await res.json()

      if (!data.success) {
        setError(data.error || "Une erreur est survenue")
        toast({
          title: "Erreur",
          description: data.error || "Échec de la requête",
          status: "error",
          duration: 5000,
        })
        return
      }

      setAnswer(data.answer || "")
      setDocuments(data.documents || [])

      toast({
        title: "Succès",
        description: "Réponse générée avec succès",
        status: "success",
        duration: 3000,
      })
    } catch (err) {
      console.error(err)
      setError("Erreur de connexion au serveur")
      toast({
        title: "Erreur",
        description: "Impossible de contacter le serveur",
        status: "error",
        duration: 5000,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !isLoading) {
      handleSearch()
    }
  }

  return (
    <Box minH="100vh" bg="#0f0f0f">
      <Container maxW="container.lg" py={10}>
        <VStack spacing={8} align="stretch">
          {/* Titre principal */}
          <Heading textAlign="center" size="xl" color="#e5e7eb">
            OCR RAG Assistant
          </Heading>

          {/* Carte de recherche */}
          <Card
            bg="#1a1a1a"
            boxShadow="0 4px 6px rgba(0, 0, 0, 0.3)"
            borderRadius="2xl"
            borderWidth="1px"
            borderColor="#374151"
          >
            <CardBody>
              <VStack spacing={4} align="stretch">
                <Heading size="md" color="#e5e7eb">
                  Posez votre question
                </Heading>

                <InputGroup size="lg">
                  <Input
                    placeholder="Ex: Comment installer Tesseract OCR?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    pr="4.5rem"
                    disabled={isLoading}
                    bg="#1f2937"
                    color="#e5e7eb"
                    borderColor="#374151"
                    _placeholder={{ color: "#9ca3af" }}
                    _focus={{ borderColor: "#6b7280", boxShadow: "0 0 0 1px #6b7280" }}
                  />
                  <InputRightElement width="4.5rem">
                    <Button
                      h="1.75rem"
                      size="sm"
                      bg="#374151"
                      color="#f3f4f6"
                      onClick={handleSearch}
                      isLoading={isLoading}
                      disabled={isLoading}
                      _hover={{ bg: "#4b5563" }}
                    >
                      <SearchIcon />
                    </Button>
                  </InputRightElement>
                </InputGroup>

                {/* Loading */}
                {isLoading && (
                  <Box textAlign="center" py={4}>
                    <Spinner size="lg" color="#6b7280" />
                    <Text mt={2} color="#9ca3af">
                      Recherche en cours...
                    </Text>
                  </Box>
                )}

                {/* Erreur */}
                {error && !isLoading && (
                  <Alert status="error" borderRadius="md" bg="#7f1d1d" borderColor="#dc2626" borderWidth="1px">
                    <AlertIcon color="#fca5a5" />
                    <Box>
                      <AlertTitle color="#fca5a5">Erreur</AlertTitle>
                      <AlertDescription color="#fee2e2">{error}</AlertDescription>
                    </Box>
                  </Alert>
                )}

                {/* Réponse */}
                {answer && !isLoading && (
                  <Card bg="#1f2937" borderRadius="lg" borderWidth="1px" borderColor="#374151">
                    <CardBody>
                      <Heading size="sm" mb={2} color="#e5e7eb">
                        💡 Réponse
                      </Heading>
                      <Text color="#d1d5db">{answer}</Text>
                    </CardBody>
                  </Card>
                )}

                {/* Documents sources */}
                {documents.length > 0 && !isLoading && (
                  <Card bg="#1a1a1a" borderRadius="lg" borderWidth="1px" borderColor="#374151">
                    <CardBody>
                      <Heading size="sm" mb={3} color="#e5e7eb">
                        📚 Sources ({documents.length})
                      </Heading>
                      <VStack spacing={2} align="stretch">
                        {documents.map((doc, i) => (
                          <Box key={i} p={3} bg="#1f2937" borderRadius="md" borderWidth="1px" borderColor="#374151">
                            <Text fontSize="sm" fontWeight="bold" color="#e5e7eb">
                              {doc.path}
                            </Text>
                            <Text fontSize="xs" color="#9ca3af">
                              Score: {doc.score.toFixed(4)}
                            </Text>
                          </Box>
                        ))}
                      </VStack>
                    </CardBody>
                  </Card>
                )}
              </VStack>
            </CardBody>
          </Card>
        </VStack>
      </Container>
    </Box>
  )
}
